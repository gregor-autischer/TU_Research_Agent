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
            }
        },
    },
    plugins: [],
}
