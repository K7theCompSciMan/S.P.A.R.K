/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{svelte, html, js, ts}'],
	theme: {
		extend: {
			colors: {
				dark: {
					primary: '#8c8df1',
					secondary: '#66139a',
					accent: '#bb25e4',
					success: '#31e425',
					fail: '#f90000',
					warning: '#f98100',
					background: {
						800: '#04051f',
						600: '#0F051f',
						500: '#2F051f',
						300: '#843b5e'
					},
					text: '#d3d6fa'
				},
				light: {
					primary: '#0e1071',
					secondary: '#b865ec',
					accent: '#b11bda',
					success: '#31e425',
					fail: '#f90000',
					warning: '#f98100',
					background: {
						default: '#dfe0fb'
					},
					text: '#05082e'
				}
			}
		}
	},
	plugins: [import('tailwind-scrollbar-hide')]
};
