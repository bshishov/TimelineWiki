import Vue from 'vue'
import Router from 'vue-router'
import MainPage from '@/components/MainPage';
import RealmPage from '@/components/RealmPage';

Vue.use(Router);

export default new Router({
  mode: 'history',
  scrollBehavior(to, from, savedPosition) {
		if (to.hash) {
			return { selector: to.hash }
		} else if (savedPosition) {
    		return savedPosition;
    	} else {
			return { x: 0, y: 0 }
		}
	},
  routes: [
    { path: '/', name: MainPage.name, component: MainPage },
    { path: '/realms/:uri', name: RealmPage.name, component: RealmPage }
  ]
})
