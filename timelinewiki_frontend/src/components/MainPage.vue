<template>
  <div class="container">
    <div v-for="realm in realms" :key="realm.uri" v-if="!loadInProgress">
      <router-link tag="a" :to="{ name: 'RealmPage', params: {uri: realm.uri }}">
        {{ realm.name }}
      </router-link>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'MainPage',
    data () {
      return {
        realms: [],
        loadInProgress: true,
      }
    },
    mounted () {
      this.loadInProgress = true;
      this.$http.get("/").then(r => {
        this.realms = r.data;
        this.loadInProgress = false;
      });
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
