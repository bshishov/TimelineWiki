<template>
    <div class="events-list">
      <EventCard v-for="event in events" :key="event.id" :event="event"/>
    </div>
</template>

<script>
  import EventCard from "./EventCard";

  export default {
    components: {EventCard},
    props: ['events'],
    name: "EventList",
    computed: {},
    data() {
      return {}
    },
    created() {},
    mounted() {}
  }
</script>

<style scoped>
  .events-list {
    display: flex;
    flex-flow: column nowrap;
    align-items: stretch;
    justify-content: flex-start;
  }
</style>
