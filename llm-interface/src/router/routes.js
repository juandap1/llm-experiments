const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'stocks', component: () => import('pages/StocksPage.vue') },
      { path: 'stocks/:ticker', component: () => import('pages/IndividualStockPage.vue') },
    ],
  },
  {
    path: '/learning',
    component: () => import('layouts/LearningLayout.vue'),
    children: [
      { path: '', component: () => import('pages/Learning/IndexPage.vue') },
      { path: 'curriculum', component: () => import('pages/Learning/CurriculumPage.vue') },
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
