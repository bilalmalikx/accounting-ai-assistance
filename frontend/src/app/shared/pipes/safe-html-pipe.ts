import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Pipe({
  name: 'safeHtml',
  standalone: true
})
export class SafeHtmlPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}

  transform(value: string | null | undefined): SafeHtml {
    if (!value) {
      return '';
    }
    
    // Convert to string if it's something else
    let stringValue = typeof value === 'string' ? value : String(value);
    
    // Clean the string - preserve meaningful content
    let cleaned = stringValue
      // Remove the problematic "SafeValue" error text that might be in the string
      .replace(/SafeValue must use \[property]=binding: /g, '')
      // Remove Angular's security warning comments
      .replace(/\(see https:\/\/angular\.dev\/best-practices\/security[^)]*\)/g, '')
      // Replace multiple spaces with single space
      .replace(/\s+/g, ' ')
      // Trim whitespace
      .trim();
    
    // Now manually convert line breaks and formatting
    let withBreaks = cleaned
      // Replace literal \n with <br>
      .replace(/\\n/g, '<br>')
      // Replace actual newlines with <br>
      .replace(/\n/g, '<br>')
      // Replace multiple dots (ellipsis) with proper formatting
      .replace(/\.{3,}/g, '…');
    
    // Mark as trusted HTML
    return this.sanitizer.bypassSecurityTrustHtml(withBreaks);
  }
}