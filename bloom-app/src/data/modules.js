export const MODULES = [
  {
    id: 'cycle',
    label: 'Cycle',
    icon: 'MoonStar',
    color: 'var(--rose-400)',
    bg: 'var(--rose-50)',
    activeColor: 'var(--rose-600)',
    welcome: {
      title: 'Cycle companion',
      description: 'Track patterns, understand your pain, and get sourced answers about your menstrual health.',
    },
    starters: [
      { icon: '🌙', text: 'I have really painful periods — is this normal?' },
      { icon: '📅', text: 'My cycle has been irregular for 3 months' },
      { icon: '💊', text: 'What are my options for managing cramps at work?' },
      { icon: '🔍', text: 'Could my symptoms indicate endometriosis?' },
    ],
  },
  {
    id: 'conception',
    label: 'Conception',
    icon: 'Heart',
    color: 'var(--lav-600)',
    bg: 'var(--lav-50)',
    activeColor: 'var(--lav-800)',
    welcome: {
      title: 'Conception support',
      description: 'Fertility guidance, IVF support, and help balancing treatment with your professional life.',
    },
    starters: [
      { icon: '❤️', text: 'I want to start trying — what should I know?' },
      { icon: '🏥', text: 'I have egg retrieval Thursday but a meeting at 10' },
      { icon: '📋', text: 'What are my IVF absence rights at work?' },
      { icon: '💬', text: 'How do I talk to my manager without revealing why?' },
    ],
  },
  {
    id: 'menopause',
    label: 'Menopause',
    icon: 'Leaf',
    color: 'var(--sage-400)',
    bg: 'var(--sage-50)',
    activeColor: 'var(--sage-600)',
    welcome: {
      title: 'Menopause guide',
      description: 'Navigate perimenopause and menopause with evidence-based answers and workplace strategies.',
    },
    starters: [
      { icon: '🍃', text: 'I can\'t concentrate in afternoon meetings anymore' },
      { icon: '🌡️', text: 'Hot flashes at work — how do others manage?' },
      { icon: '💤', text: 'Sleep disruption is affecting my performance' },
      { icon: '⚖️', text: 'What are the benefits and risks of HRT?' },
    ],
  },
  {
    id: 'breast',
    label: 'Breast health',
    icon: 'Ribbon',
    color: 'var(--rose-400)',
    bg: 'var(--rose-50)',
    activeColor: 'var(--rose-600)',
    welcome: {
      title: 'Breast health companion',
      description: 'Self-exam guidance, screening reminders, and risk-aware support — early detection saves lives.',
    },
    starters: [
      { icon: '🎀', text: 'Guide me through a self-exam' },
      { icon: '📆', text: 'When should I schedule my next mammogram?' },
      { icon: '👩‍👧', text: 'My mother had breast cancer — what\'s my risk?' },
      { icon: '❓', text: 'I found something unusual — what should I do?' },
    ],
  },
];
