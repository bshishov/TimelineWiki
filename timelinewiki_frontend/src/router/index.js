import Vue from 'vue'
import Router from 'vue-router'
import MainPage from '@/components/MainPage';
import RealmPage from '@/components/RealmPage';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    { path: '/', name: MainPage.name, component: MainPage },
    { path: '/realms/:uri', name: RealmPage.name, component: RealmPage }
  ]
})
