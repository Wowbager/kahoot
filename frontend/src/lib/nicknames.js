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

export function lameNickname() {
  return `${pick(ADJECTIVES)} ${pick(NOUNS)}`;
}

const FIRST = [
  "to je",
  "Marvánek",
  "EVA",
  "PETR",
  "my jsme",
  "po krásné cestě",
  "soudruh Sahur",
  "Sahurek",
  "triple T",
  "Očí",
  "Očíčko",
  "Kolí",
  "Koláček",
  "SSSSSSSSS",
  "bro",
  "čau, já jsem",
  "jáj děcka",
  "na prahu"
];

const SECOND = [
  "z centra dojeďte",
  "EVA",
  "PETR",
  "Petr Fiala",
  "Karel Kirk",
  "Marvánek",
  "centrum",
  "k němu",
  "zpátky do centra",
  "Marvánek",
  "ČESKO",
  "TESCO",
  "ve stavu blaženosti",
  "Becquerel"
]

export function randomNickname() {
  return `${pick(FIRST)} ${pick(SECOND)}`;
}