
function updateFontScaler() {
    const container = document.getElementById('food_content');

    if (container) {
        const containerWidth = container.offsetWidth;
        const fontScaler = containerWidth * 0.004; // Adjust the multiplier as needed

        document.documentElement.style.setProperty('--font-scaler', fontScaler);
    }
}

document.addEventListener('DOMContentLoaded', updateFontScaler);
window.addEventListener('resize', updateFontScaler);
