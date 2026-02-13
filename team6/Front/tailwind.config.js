/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Colors extracted from your uploaded images
                primary: {
                    DEFAULT: '#F97316', // The Orange button color
                    hover: '#EA580C',
                    light: '#FFF7ED', // Light orange background
                },
                secondary: {
                    DEFAULT: '#3B82F6', // The Blue accent color
                    dark: '#1D4ED8',
                    light: '#EFF6FF', // Light blue background
                },
                dark: {
                    900: '#111827', // Main text
                    800: '#1F2937',
                    500: '#6B7280', // Muted text
                },
                bg: {
                    main: '#F3F4F6', // The light grey background of the dashboard
                    card: '#FFFFFF',
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'], // Standard modern font
            },
            boxShadow: {
                'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
            }
        },
    },
    plugins: [],
}