<template>
    <div class="events-list">
      <EventCard v-for="(event, index) in events"
                 :key="event.id"
                 :event="event"
                 :editable="editable"
                 @remove="remove(index)"
      />
      <div class="button create" @click="appendNew"><i class="fas fa-plus"/></div>
    </div>
</template>

<script>
  import EventCard from "./EventCard";
  import EventEditor from "./EventEditor";

  export default {
    components: {EventCard, EventEditor},
    props: {
      events: {
        type: Array,
        required: false,
        default: []
      },
      editable: {
        type: Boolean,
        required: false,
        default: true
      },
      realm: {
        type: String,
        required: false,
        default: undefined
      }
    },
    name: "EventList",
    computed: {
      canAdd: function () {
        return this.editable && typeof this.realm !== 'undefined'
      }
    },
    data() { return {} },
    created() {},
    mounted() {},
    methods: {
      insertEvent: function (index, event) {
        let previous = this.$props.events[index - 1];
        let next = this.$props.events[index];
        if (typeof previous !== 'undefined')
        {
          if(typeof next !== 'undefined') {
            event.order = previous.order + 0.5 * (next.order - previous.order);
          }
          else {
           event.order = previous.order + 1;
          }
        } else {
          event.order = 0;
        }
        this.$props.events.splice(index, 0, event);
      },
      appendEvent: function (event) {
        this.insertEvent(this.$props.events.length, event)
      },
      appendNew: function () {
        this.appendEvent({
          type: 'text',
          value: '',
          realm: this.realm,
          order: 0
        })
      },
      remove: function (index) {
        this.$props.events.splice(index, 1);
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../main.scss";

  .events-list {
    display: flex;
    flex-flow: column nowrap;
    align-items: stretch;
    justify-content: flex-start;

    .button.create {
      margin: 1em auto;
      padding: 8px 16px;
      /*width: 60px;*/
      text-align: center;
      border-radius: 100px;
      border: 1px solid $color4;
      color: $color4;
      background-color: white;
      cursor: pointer;
    }
  }
</style>
