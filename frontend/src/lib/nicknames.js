// Friendly two-word nickname generator (client-side, à la Kahoot).
// Keeps names short so they stay under the 30-char server limit.

const ADJECTIVES = [
  'Brave', 'Sneaky', 'Turbo', 'Wobbly', 'Sparkly', 'Mighty', 'Cosmic', 'Fuzzy',
  'Zippy', 'Cheeky', 'Jolly', 'Swift', 'Funky', 'Spicy', 'Bouncy', 'Dizzy',
  'Groovy', 'Witty', 'Lucky', 'Sunny', 'Daring', 'Gentle', 'Quirky', 'Nimble',
  'Bubbly', 'Cuddly', 'Epic', 'Goofy', 'Snappy', 'Velvet',
];

const NOUNS = [
  'Otter', 'Penguin', 'Waffle', 'Comet', 'Pickle', 'Dragon', 'Noodle', 'Falcon',
  'Muffin', 'Tiger', 'Cactus', 'Walrus', 'Panda', 'Rocket', 'Pixel', 'Mango',
  'Wizard', 'Llama', 'Yeti', 'Robot', 'Koala', 'Nugget', 'Phoenix', 'Bagel',
  'Hedgehog', 'Donut', 'Narwhal', 'Gizmo', 'Sprout', 'Goblin',
];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function randomNickname() {
  return `${pick(ADJECTIVES)} ${pick(NOUNS)}`;
}
