/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {
            fontFamily: {
                inter: ['InterVariable', 'Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
            },
            colors: {
                'forest-floor': '#0e231c',
                'canopy-shadow': '#1a3029',
                'pine-border': '#233630',
                'slate-ink': '#313942',
                'ash': '#656a75',
                'mist': '#c3cecb',
                'fog': '#879b93',
                'parchment': '#f4f7f2',
                'dew': '#e4ebe2',
                'sprout': '#27ae60',
                'sage-whisper': '#defaca',
                'mint-card': '#edf9f2',
                'iris': '#5c51e0',
                'sky-link': '#186bff',
                'tangerine-cta': '#ff5722',
                'amber-nav': '#f49a40',
                'azure-action': '#2f80ed',
                'lavender-tint': '#f1ebff',
            },
            fontSize: {
                'caption': ['11px', { lineHeight: '2.29', letterSpacing: '1.3px' }],
                'body-sm': ['14px', { lineHeight: '1.5' }],
                'body': ['16px', { lineHeight: '1.6' }],
                'subheading': ['18px', { lineHeight: '1.5' }],
                'heading-sm': ['24px', { lineHeight: '1.35', letterSpacing: '-0.24px' }],
                'heading': ['32px', { lineHeight: '1.3', letterSpacing: '-0.48px' }],
                'heading-lg': ['48px', { lineHeight: '1.1', letterSpacing: '-1.06px' }],
                'display': ['57px', { lineHeight: '1', letterSpacing: '-1.6px' }],
            },
            borderRadius: {
                'tags': '5px',
                'cards': '32px',
                'chips': '17px',
                'badges': '6px',
                'images': '12px',
                'buttons': '999px',
            },
            boxShadow: {
                'xl': 'rgba(17, 50, 38, 0.14) 14px 17px 40px 0px',
                'subtle': 'rgb(236, 239, 243) 1px 0px 0px 0px inset',
                'subtle-2': 'rgb(236, 239, 243) 0px -1px 0px 0px inset',
                'xl-2': 'rgba(17, 50, 38, 0.14) 14px 48px 40px 0px',
                'lg': 'rgba(10, 33, 65, 0.05) 0px 10px 20px 0px, rgba(0, 0, 0, 0.13) 0px 0px 2px 0px',
            },
            spacing: {
                '4': '4px',
                '8': '8px',
                '12': '12px',
                '16': '16px',
                '20': '20px',
                '24': '24px',
                '28': '28px',
                '32': '32px',
                '36': '36px',
                '40': '40px',
                '60': '60px',
                '64': '64px',
                '80': '80px',
                '100': '100px',
                '136': '136px',
                '140': '140px',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}