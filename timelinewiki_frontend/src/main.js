import Vue from 'vue'
import App from './App'
import router from './router'
import store from "./store"
import Axios from 'axios'
import showdown from 'showdown';

Vue.config.productionTip = false;
Axios.defaults.baseURL = 'http://localhost:5000/';

Vue.prototype.$showdown = new showdown.Converter({
  ghMentions: true,
  ghMentionsLink: 'http://google.com/q={u}'
});
Vue.prototype.$http = Axios;

new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
});
