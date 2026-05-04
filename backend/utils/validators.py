"""Validation Utilities for Indian Financial Documents"""
import re
from typing import Tuple, Optional

class Validators:
    """Collection of validation methods for Indian financial entities"""
    
    @staticmethod
    def validate_pan_number(pan: str) -> Tuple[bool, Optional[str]]:
        """Validate Indian PAN card number"""
        if not pan:
            return False, "PAN number is empty"
        
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if re.match(pattern, pan.upper()):
            return True, None
        return False, "Invalid PAN format. Expected: ABCDE1234F"
    
    @staticmethod
    def validate_gst_number(gst: str) -> Tuple[bool, Optional[str]]:
        """Validate Indian GST number"""
        if not gst:
            return False, "GST number is empty"
        
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if re.match(pattern, gst.upper()):
            return True, None
        return False, "Invalid GST format"
    
    @staticmethod
    def validate_ifsc_code(ifsc: str) -> Tuple[bool, Optional[str]]:
        """Validate IFSC code"""
        if not ifsc:
            return False, "IFSC code is empty"
        
        pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        if re.match(pattern, ifsc.upper()):
            return True, None
        return False, "Invalid IFSC format. Expected: ABCD0123456"
    
    @staticmethod
    def validate_account_number(account_number: str) -> Tuple[bool, Optional[str]]:
        """Validate bank account number"""
        if not account_number:
            return False, "Account number is empty"
        
        clean = re.sub(r'[\s\-]', '', account_number)
        if len(clean) >= 9 and len(clean) <= 18 and clean.isdigit():
            return True, None
        return False, "Account number should be 9-18 digits"
    
    @staticmethod
    def validate_amount(amount: str) -> Tuple[bool, Optional[float]]:
        """Validate and convert amount"""
        try:
            cleaned = re.sub(r'[^\d\.\-]', '', amount)
            value = float(cleaned)
            if value < 0:
                return False, None
            return True, value
        except ValueError:
            return False, None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address"""
        if not email:
            return False, "Email is empty"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, None
        return False, "Invalid email format"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Validate Indian phone number"""
        if not phone:
            return False, "Phone number is empty"
        
        clean = re.sub(r'[\s\+\-\(\)]', '', phone)
        pattern = r'^[6-9]\d{9}$'
        if re.match(pattern, clean):
            return True, None
        return False, "Invalid Indian phone number"
    
    @staticmethod
    def validate_financial_year(year_str: str) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """Validate financial year format (YYYY-YY)"""
        pattern = r'^(\d{4})-(\d{2})$'
        match = re.match(pattern, year_str)
        
        if match:
            start_year = int(match.group(1))
            end_suffix = int(match.group(2))
            expected_end = (start_year + 1) % 100
            if end_suffix == expected_end:
                return True, (start_year, start_year + 1)
        
        return False, None