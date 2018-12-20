<template>
    <div class="container">
      <Outline :events="events"></Outline>
      <h1>{{ realm.name }}</h1>
      <EventList
        :events="events"
        :realm="realm.uri"
        v-if="!loadInProgress" />
      <Loader v-else></Loader>
    </div>
</template>

<script>
  import EventList from "./EventList";
  import Loader from "./Loader";
  import Outline from "./Outline";

  export default {
    name: "RealmPage",
    components: {Outline, EventList, Loader},
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
