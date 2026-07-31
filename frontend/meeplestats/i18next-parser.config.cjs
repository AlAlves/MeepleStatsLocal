module.exports = {
  locales: ['fr', 'en', 'de', 'it' ],

  input: ['src/**/*.{ts,tsx}'],
  output: './public/locales/$LOCALE/$NAMESPACE.json',
  defaultNamespace: 'translation',
  createOldCatalogs: false,
  keepRemoved: false,
  sort: true,
  verbose: true,
};