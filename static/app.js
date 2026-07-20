(() => {
  const form = document.querySelector('.questionnaire');
  const steps = [...document.querySelectorAll('.form-step')];
  const navButtons = [...document.querySelectorAll('.step-button')];
  const previous = document.getElementById('previous_step');
  const next = document.getElementById('next_step');
  const generate = document.getElementById('generate_button');
  const progress = document.getElementById('progress_bar');
  let current = 0;

  function restorePreviousValues() {
    const stateElement = document.getElementById('previous_form_data');
    if (!form || !stateElement) return;

    let values = {};
    try {
      values = JSON.parse(stateElement.textContent || '{}');
    } catch (_error) {
      return;
    }

    for (const [name, value] of Object.entries(values)) {
      const fields = [...form.elements].filter(field => field.name === name);
      for (const field of fields) {
        if (field.type === 'file') continue;
        if (field.type === 'checkbox' || field.type === 'radio') {
          field.checked = field.value === value || ['on', 'true', '1', 'yes'].includes(String(value).toLowerCase());
        } else {
          field.value = value;
        }
      }
    }
  }

  function showStep(index) {
    if (!steps.length) return;
    current = Math.max(0, Math.min(index, steps.length - 1));
    steps.forEach((step, i) => step.classList.toggle('active', i === current));
    navButtons.forEach((button, i) => button.classList.toggle('active', i === current));
    previous.disabled = current === 0;
    next.classList.toggle('hidden', current === steps.length - 1);
    generate.classList.toggle('hidden', current !== steps.length - 1);
    progress.style.width = `${((current + 1) / steps.length) * 100}%`;
    window.scrollTo({ top: document.querySelector('.questionnaire').offsetTop - 88, behavior: 'smooth' });
  }

  function validateCurrentStep() {
    if (!steps.length) return true;
    const required = [...steps[current].querySelectorAll('[required]')];
    for (const field of required) {
      if (!field.checkValidity()) {
        field.reportValidity();
        return false;
      }
    }
    return true;
  }

  next?.addEventListener('click', () => {
    if (validateCurrentStep()) showStep(current + 1);
  });
  previous?.addEventListener('click', () => showStep(current - 1));
  navButtons.forEach((button, index) => button.addEventListener('click', () => {
    if (index <= current || validateCurrentStep()) showStep(index);
  }));

  const type = document.getElementById('presentation_type');
  const orgToggle = document.getElementById('organisation_enabled');
  const orgInputs = document.querySelector('.organisation-inputs');
  const orgName = document.getElementById('organisation_name');
  const orgRequired = document.querySelector('.organisation-required');

  function syncOrganisation() {
    if (!type || !orgToggle || !orgInputs || !orgName) return;

    const internship = type.value === 'internship';
    if (internship) orgToggle.checked = true;
    else if (type.value === 'school_project' && !orgToggle.dataset.userChanged) orgToggle.checked = false;

    orgToggle.disabled = internship;
    orgToggle.setAttribute('aria-disabled', internship ? 'true' : 'false');

    const enabled = internship || orgToggle.checked;
    orgInputs.classList.toggle('disabled', !enabled);
    orgInputs.querySelectorAll('input').forEach(input => {
      input.disabled = !enabled;
    });
    orgName.required = enabled;
    orgRequired?.classList.toggle('hidden', !enabled);
  }

  type?.addEventListener('change', syncOrganisation);
  orgToggle?.addEventListener('change', () => {
    orgToggle.dataset.userChanged = 'true';
    syncOrganisation();
  });

  restorePreviousValues();
  syncOrganisation();

  document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
      const container = button.closest('.panel, .instructions-preview');
      if (!container) return;
      container.querySelectorAll('.tab-button').forEach(item => item.classList.remove('active'));
      container.querySelectorAll('.tab-panel').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      document.getElementById(button.dataset.tab)?.classList.add('active');
    });
  });

  const initialStep = Number.parseInt(form?.dataset.initialStep || '1', 10);
  showStep(Number.isFinite(initialStep) ? initialStep - 1 : 0);
})();
