const RESPONSES = {

};

export function getResponse(userMessage) {
  const key = Object.keys(RESPONSES).find(
    (k) => k.toLowerCase() === userMessage.toLowerCase()
  );
  if (key) return RESPONSES[key];

  const partialKey = Object.keys(RESPONSES).find((k) =>
    userMessage.toLowerCase().includes(k.slice(0, 20).toLowerCase())
  );
  if (partialKey) return RESPONSES[partialKey];

  return {
    text: 'I\'m here to help with your health questions. I\'ll always ground my answers in medical guidelines and your workplace policies. Could you tell me more about what you\'re experiencing?',
    source: 'Bloom knowledge base',
    chips: ['Track my symptoms', 'My rights at work', 'Find a specialist', 'Set a health reminder'],
  };
}
