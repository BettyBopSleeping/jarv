import re
from datetime import datetime, timedelta

class DateParser:
    @staticmethod
    def parse_date(date_string):
        """
        Parse various date formats
        
        :param date_string: String representing a date
        :return: Parsed date or None
        """
        # Direct date parsing (YYYY-MM-DD)
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            pass
        
        # Relative date parsing
        today = datetime.now().date()
        
        # Check for specific relative dates
        relative_mappings = {
            'today': today,
            'tomorrow': today + timedelta(days=1)
        }
        
        if date_string.lower() in relative_mappings:
            return relative_mappings[date_string.lower()]
        
        # Parse relative time periods
        relative_period_match = re.match(r'(\d+)\s*(day|week|month)s?\s*from\s*now', date_string, re.IGNORECASE)
        if relative_period_match:
            number = int(relative_period_match.group(1))
            unit = relative_period_match.group(2).lower()
            
            if unit == 'day':
                return today + timedelta(days=number)
            elif unit == 'week':
                return today + timedelta(weeks=number)
            elif unit == 'month':
                return today + timedelta(days=number*30)
        
        return None