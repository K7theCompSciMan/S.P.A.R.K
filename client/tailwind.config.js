/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
	  extend: {
		colors: {
		  dark: {
			background: {
			  50: '#fafafa',
			  100: '#f4f4f5',
			  200: '#e4e4e7',
			  300: '#d4d4d8',
			  400: '#a1a1aa',
			  500: '#71717a',
			  600: '#52525b',
			  700: '#27272a',
			  800: '#18181b', // Card slate
			  900: '#09090b', // Base canvas background
			  950: '#030303'  // Pure obsidian deep background
			},
			primary: '#3b82f6', // Premium deep electric blue
			secondary: '#6366f1', // Rich indigo highlight
			accent: '#a855f7', // Vibrant royal violet accent
			text: '#f4f4f5'
		  }
		},
		fontFamily: {
		  sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
		  mono: ['JetBrains Mono', 'Fira Code', 'monospace']
		}
	  }
	},
	plugins: []
  };