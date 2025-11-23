const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'stocks', component: () => import('pages/Stocks/StocksPage.vue') },
      { path: 'stocks/assets', component: () => import('pages/Stocks/StockAssetPage.vue') },
      { path: 'stocks/news', component: () => import('pages/Stocks/StocksPage.vue') },
      { path: 'stocks/history', component: () => import('pages/Stocks/StocksPage.vue') },
      {
        path: 'stocks/ticker/:ticker',
        component: () => import('pages/Stocks/IndividualStockPage.vue'),
      },
    ],
  },
  {
    path: '/learning',
    component: () => import('layouts/LearningLayout.vue'),
    children: [
      { path: '', component: () => import('pages/Learning/IndexPage.vue') },
      { path: 'topics', component: () => import('pages/Learning/TopicsPage.vue') },
      { path: 'lesson/:topicId', component: () => import('pages/Learning/LessonPage.vue') },
      { path: 'quiz', component: () => import('pages/Learning/QuizPage.vue') },
      { path: 'analytics', component: () => import('pages/Learning/AnalyticsPage.vue') },
      { path: 'notes', component: () => import('pages/Learning/MarkdownEditorPage.vue') }, // Using existing MarkdownEditorPage for notes
      { path: 'chat', component: () => import('pages/Learning/ChatPage.vue') },
      { path: 'search', component: () => import('pages/Learning/IndexPage.vue') }, // Placeholder
      { path: 'flashcards', component: () => import('pages/Learning/IndexPage.vue') }, // Placeholder
      { path: 'graph', component: () => import('pages/Learning/IndexPage.vue') }, // Placeholder
      { path: 'settings', component: () => import('pages/Learning/IndexPage.vue') }, // Placeholder
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
