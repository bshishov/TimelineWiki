<template>
    <div class="container">
      <h1>{{ realm.name }}</h1>
      <EventList v-bind:events="events" v-if="!loadInProgress" />
      <Loader v-else></Loader>
    </div>
</template>

<script>
  import EventList from "./EventList";
  import Loader from "./Loader";

  export default {
    name: "RealmPage",
    components: {EventList, Loader},
    data() {
      return {
        realm: {name: '', uri: ''},
        events: [],
        loadInProgress: true
      }
    },
    mounted() {
      let realmUri = this.$route.params.uri;
      this.$http.all([
        this.$http.get(realmUri),
        this.$http.get(realmUri + '/events')
      ])
      .then(this.$http.spread((realmResponse, eventsResponse) => {
        this.realm = realmResponse.data;
        this.events = eventsResponse.data;
        this.loadInProgress = false;
      }))
      .catch(error => {
        // TODO: 404
      });
    }
  }
</script>

<style scoped>

</style>
