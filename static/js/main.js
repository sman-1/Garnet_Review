const ratingDescs = {
  overall:       ['', 'Terrible', 'Poor', 'Okay', 'Good', 'Amazing'],
  difficulty:    ['', 'Super Easy', 'Easy', 'Moderate', 'Hard', 'Brutal'],
  teacher_rating:['', 'Very Poor', 'Below Average', 'Average', 'Good', 'Excellent'],
  workload:      ['', 'Very Light', 'Light', 'Moderate', 'Heavy', 'Very Heavy'],
};

document.querySelectorAll('.star-picker').forEach(picker => {
  const name  = picker.dataset.name;
  const stars = picker.querySelectorAll('.star-pick');
  const input = picker.querySelector('input[type=hidden]');
  const desc  = picker.querySelector('.rating-desc');
  let selected = 0;

  const paint = val => {
    stars.forEach(s => {
      s.classList.toggle('active', +s.dataset.val <= val);
    });
    if (desc && ratingDescs[name]) desc.textContent = val ? ratingDescs[name][val] : '';
  };

  stars.forEach(star => {
    star.addEventListener('mouseenter', () => paint(+star.dataset.val));
    star.addEventListener('mouseleave', () => paint(selected));
    star.addEventListener('click', () => {
      selected = +star.dataset.val;
      input.value = selected;
      paint(selected);
    });
  });
});

document.querySelectorAll('.recommend-toggle input').forEach(radio => {
  radio.addEventListener('change', () => {
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.style.fontWeight = '');
  });
});

const form = document.getElementById('reviewForm');
if (form) {
  form.addEventListener('submit', e => {
    const required = ['overall', 'difficulty', 'teacher_rating', 'workload'];
    for (const name of required) {
      const el = document.getElementById(name);
      if (!el || !el.value) {
        e.preventDefault();
        const picker = document.querySelector(`.star-picker[data-name="${name}"]`);
        if (picker) {
          picker.scrollIntoView({ behavior: 'smooth', block: 'center' });
          picker.style.outline = '2px solid #EF4444';
          picker.style.borderRadius = '8px';
          setTimeout(() => picker.style.outline = '', 2000);
        }
        return;
      }
    }
  });
}
