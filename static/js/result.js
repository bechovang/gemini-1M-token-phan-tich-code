// ============================
// result.js
// ============================
// static/js/result.js

document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.container');
  if (!container || container.dataset.analysisPresent !== 'true') return;

  const meets = JSON.parse(container.dataset.meetsRequirements);
  const seCnt = +container.dataset.syntaxErrorsCount;
  const leCnt = +container.dataset.logicalErrorsCount;
  const reCnt = +container.dataset.runtimeErrorsCount;

  // Chỉ bắn confetti khi code hoàn toàn đúng
  if (!(meets && seCnt === 0 && leCnt === 0 && reCnt === 0 && typeof confetti === 'function')) {
    return;
  }

  // Tạo một instance confetti dùng worker để performance tốt hơn
  const myConfetti = confetti.create(null, {
    resize: true,
    useWorker: true
  });

  // Mảng màu rực rỡ
  const colors = [
    '#ff595e',
    '#ffca3a',
    '#8ac926',
    '#1982c4',
    '#6a4c93',
    '#f72585',
    '#3a0ca3'
  ];

  // Hàm bắn một đợt confetti
  function launchBurst() {
    myConfetti({
      particleCount: 150,
      angle: Math.random() * 60 + 60,        // góc giữa 60–120°
      spread: Math.random() * 60 + 40,       // độ tỏa giữa 40–100°
      startVelocity: Math.random() * 30 + 20,// vận tốc ban đầu
      origin: {
        x: Math.random(),
        y: Math.random() * 0.2              // chỗ cao đầu
      },
      colors: colors,
      scalar: Math.random() * 0.6 + 0.7      // kích thước thay đổi
    });
  }

  // Bắn liên tục mỗi 300ms
  const confettiInterval = setInterval(launchBurst, 300);

  // Dừng khi người dùng click bất kỳ đâu
  function stopConfetti() {
    clearInterval(confettiInterval);
    document.removeEventListener('click', stopConfetti);
  }
  document.addEventListener('click', stopConfetti);
});
