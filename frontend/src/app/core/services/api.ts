import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, TimeoutError } from 'rxjs';
import { catchError, timeout, retry, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { AnswerResponse, QuestionRequest, UploadResponse } from '../interfaces/api';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;
  private timeoutMs = environment.apiTimeout;

  constructor(private http: HttpClient) {}

  uploadPDF(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadResponse>(`${this.apiUrl}/upload`, formData)
      .pipe(
        timeout(this.timeoutMs),
        retry(1),
        catchError(this.handleError)
      );
  }

  askQuestion(request: QuestionRequest): Observable<AnswerResponse> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    
    return this.http.post<AnswerResponse>(`${this.apiUrl}/ask`, request, { headers })
      .pipe(
        timeout(this.timeoutMs),
        retry(1),
        catchError(this.handleError)
      );
  }

  checkHealth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`)
      .pipe(
        timeout(5000),
        catchError(this.handleError)
      );
  }

  private handleError(error: HttpErrorResponse | TimeoutError) {
    let errorMessage = 'An unknown error occurred!';
    
    if (error instanceof TimeoutError) {
      errorMessage = 'Request timeout. Server might be busy.';
    } else if (error.error instanceof ErrorEvent) {
      errorMessage = error.error.message;
    } else if (error.error?.error) {
      errorMessage = error.error.error;
    } else if (error.error?.detail) {
      errorMessage = error.error.detail;
    } else if (error.status === 0) {
      errorMessage = 'Cannot connect to backend. Is the server running?';
    } else if (error.status === 413) {
      errorMessage = 'File too large. Maximum size is 50MB.';
    } else if (error.status === 400) {
      errorMessage = 'Invalid request. Check your input.';
    } else if (error.status === 500) {
      errorMessage = 'Server error. Please try again later.';
    }
    
    console.error('API Error:', error);
    return throwError(() => new Error(errorMessage));
  }
}