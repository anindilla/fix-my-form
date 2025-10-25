/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Strava-inspired warm color palette (WCAG AA compliant)
        primary: {
          50: '#fff3e0',
          100: '#ffe0b2',
          200: '#ffcc80',
          300: '#ffb74d',
          400: '#ffa726',
          500: '#ff9800', // Primary orange
          600: '#fb8c00',
          700: '#f57c00',
          800: '#ef6c00',
          900: '#e65100',
        },
        accent: {
          50: '#ffebee',
          100: '#ffcdd2',
          200: '#ef9a9a',
          300: '#e57373',
          400: '#ef5350',
          500: '#f44336', // Deep red
          600: '#e53935',
          700: '#d32f2f',
          800: '#c62828',
          900: '#b71c1c',
        },
        warm: {
          50: '#fff8e1',
          100: '#ffecb3',
          200: '#ffe082',
          300: '#ffd54f',
          400: '#ffca28',
          500: '#ffc107', // Warm yellow
          600: '#ffb300',
          700: '#ffa000',
          800: '#ff8f00',
          900: '#ff6f00',
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#eeeeee',
          300: '#e0e0e0',
          400: '#bdbdbd',
          500: '#9e9e9e',
          600: '#757575',
          700: '#616161',
          800: '#424242',
          900: '#212121', // Charcoal
        },
        success: {
          50: '#e8f5e8',
          100: '#c8e6c9',
          200: '#a5d6a7',
          300: '#81c784',
          400: '#66bb6a',
          500: '#4caf50',
          600: '#43a047',
          700: '#388e3c',
          800: '#2e7d32',
          900: '#1b5e20',
        },
        warning: {
          50: '#fff3e0',
          100: '#ffe0b2',
          200: '#ffcc80',
          300: '#ffb74d',
          400: '#ffa726',
          500: '#ff9800',
          600: '#fb8c00',
          700: '#f57c00',
          800: '#ef6c00',
          900: '#e65100',
        },
        error: {
          50: '#ffebee',
          100: '#ffcdd2',
          200: '#ef9a9a',
          300: '#e57373',
          400: '#ef5350',
          500: '#f44336',
          600: '#e53935',
          700: '#d32f2f',
          800: '#c62828',
          900: '#b71c1c',
        }
      },
          backgroundImage: {
            // Strava-inspired gradients
            'gradient-orange': 'linear-gradient(135deg, #ff9800 0%, #ff5722 100%)',
            'gradient-orange-soft': 'linear-gradient(135deg, #fff3e0 0%, #ffffff 100%)',
            'gradient-warm': 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)',
            'gradient-hero': 'linear-gradient(135deg, #fff3e0 0%, #ffffff 50%, #f5f5f5 100%)',
            'gradient-card': 'linear-gradient(135deg, #ffffff 0%, #fafafa 100%)',
            // Legacy gradients (for backward compatibility)
            'gradient-teal-blue': 'linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%)',
            'gradient-teal-blue-soft': 'linear-gradient(135deg, #f0f9ff20 0%, #ffffff20 100%)',
          },
          fontFamily: {
            'heading': ['Space Grotesk', 'system-ui', 'sans-serif'],
            'body': ['Inter', 'system-ui', 'sans-serif'],
          },
          fontSize: {
            'xs': ['12px', '16px'],
            'sm': ['14px', '20px'],
            'base': ['16px', '24px'],
            'lg': ['18px', '28px'],
            'xl': ['20px', '28px'],
            '2xl': ['24px', '32px'],
            '3xl': ['30px', '36px'],
            '4xl': ['36px', '40px'],
            '5xl': ['48px', '1'],
            '6xl': ['60px', '1'],
            '7xl': ['72px', '1'],
          },
          spacing: {
            '18': '4.5rem',
            '88': '22rem',
          },
          boxShadow: {
            'strava': '0 4px 20px rgba(255, 152, 0, 0.15)',
            'strava-lg': '0 8px 30px rgba(255, 152, 0, 0.2)',
            'card': '0 2px 8px rgba(0, 0, 0, 0.1)',
            'card-hover': '0 8px 25px rgba(0, 0, 0, 0.15)',
          }
    },
  },
  plugins: [],
}
