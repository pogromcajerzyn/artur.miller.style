function daysSinceDate(targetDate) {
    const currentDate = new Date();
    const targetDateTime = targetDate.getTime();
    const currentDateTime = currentDate.getTime();
    const timeDifference = currentDateTime - targetDateTime;
    const daysDifference = Math.floor(timeDifference / (1000 * 3600 * 24));
    return daysDifference;
}

const targetDate = new Date('2022-10-24'); // I started lifting that day
const daysSince = daysSinceDate(targetDate);
const daysCounterElement = document.getElementById('daysCounter');
daysCounterElement.textContent = `${daysSince} days`;


function updateFontScaler() {
    const container = document.getElementById('strength_content');

    if (container) {
        const containerWidth = container.offsetWidth;
        const fontScaler = containerWidth * 0.004; // Adjust the multiplier as needed

        document.documentElement.style.setProperty('--font-scaler', fontScaler);
    }
}

document.addEventListener('DOMContentLoaded', updateFontScaler);
window.addEventListener('resize', updateFontScaler);
