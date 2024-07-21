document.addEventListener('DOMContentLoaded', () => {
    const bubbles = document.querySelectorAll('.chat-bubble');
    bubbles.forEach((bubble, index) => {
        bubble.style.animationDelay = `${index * 0.5}s`;
    });
});
