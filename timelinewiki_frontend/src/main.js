import Vue from 'vue'
import App from './App'
import router from './router'
import store from "./store"
import Axios from 'axios'

Vue.config.productionTip = false;
Vue.prototype.$http = Axios;
Axios.defaults.baseURL = 'http://localhost:5000/';

new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
});
