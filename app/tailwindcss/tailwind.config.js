import daisyui from "daisyui";

export default {
    content: ["../../templates/**/*.html"],
    safelist: [
        "alert-error",
        "alert-success",
        "alert-info",
        "alert",          // base alert class
        "btn-sm",
        "btn-ghost"
    ],

    plugins: [daisyui],
    daisyui: {
        themes: [
            {
                aic: {
                    "primary": "#C8102E",
                    "secondary": "#6E6E6E",
                    "accent": "#000000",
                    "neutral": "#FFFFFF",
                    "base-100": "#FFFFFF",
                    "info": "#3B82F6",
                    "success": "#22C55E",
                    "error": "#DC2626"
                }
            },
            "light",
            "dark"
        ]
    }
};
