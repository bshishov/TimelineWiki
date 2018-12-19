import axios from 'axios'

const AUTH_TOKEN_KEY = 'authToken';

// Mutations
const AUTH_STARTED = "AUTH_STARTED";
const AUTH_SUCCESS = "AUTH_SUCCESS";
const AUTH_LOGOUT = "AUTH_LOGOUT";
const AUTH_ERROR = "AUTH_ERROR";

export default {
  namespaced: true,
  state: {
    status: '',
    token: localStorage.getItem(AUTH_TOKEN_KEY) || '',
    user : {}
  },
  mutations: {
    [AUTH_STARTED] (state) {
      state.status = 'started';
    },
    [AUTH_SUCCESS] (state, token) {
      state.status = 'success';
      state.token = token;
    },
    [AUTH_ERROR] (state) {
      state.status = 'error';
    },
    [AUTH_LOGOUT] (state) {
      state.status = '';
      state.token = '';
    },
  },
  actions: {
    login({commit}, credentials) {
      return new Promise((resolve, reject) => {
        commit(AUTH_STARTED);
        axios({url: 'auth', data: credentials, method: 'POST'})
         .then(resp => {
            const token = resp.data.token;
            const user = resp.data.user;
            localStorage.setItem(AUTH_TOKEN_KEY, token);
            axios.defaults.headers.common['Authorization'] = token;
            commit(AUTH_SUCCESS, token, user);
            resolve(resp);
         })
         .catch(err => {
            commit(AUTH_ERROR);
            localStorage.removeItem(AUTH_TOKEN_KEY);
            reject(err);
          })
      });
    },
    logout({commit}){
      return new Promise((resolve, reject) => {
        commit(AUTH_LOGOUT);
        localStorage.removeItem(AUTH_TOKEN_KEY);
        delete axios.defaults.headers.common['Authorization'];
        resolve();
      });
    }
  },
  getters : {
    authStatus: state => state.status,
    userId: state => state.user? state.user['sub'] : undefined,
    userRole: state => state.user? state.user['role'] : undefined,
    userName: state => state.user? state.user['sub'] : undefined,
    isAdmin: state => state.user? state.user['role'] === 'admin': false,
  }
}
