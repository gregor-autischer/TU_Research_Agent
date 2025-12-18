/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#ffffff',
                secondary: '#f8fafc', // Slate 50
                accent: '#2563eb', // Blue 600
            },
            typography: {
                DEFAULT: {
                    css: {
                        maxWidth: 'none',
                        color: '#1e293b',
                        p: {
                            marginTop: '0.5em',
                            marginBottom: '0.5em',
                        },
                        'ul, ol': {
                            marginTop: '0.5em',
                            marginBottom: '0.5em',
                        },
                        li: {
                            marginTop: '0.25em',
                            marginBottom: '0.25em',
                        },
                        'code::before': {
                            content: '""',
                        },
                        'code::after': {
                            content: '""',
                        },
                        code: {
                            backgroundColor: '#f1f5f9',
                            padding: '0.2em 0.4em',
                            borderRadius: '0.25rem',
                            fontWeight: '400',
                        },
                        pre: {
                            backgroundColor: '#1e293b',
                            color: '#e2e8f0',
                        },
                        strong: {
                            color: '#0f172a',
                            fontWeight: '600',
                        },
                        a: {
                            color: '#2563eb',
                            textDecoration: 'underline',
                        },
                    },
                },
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
