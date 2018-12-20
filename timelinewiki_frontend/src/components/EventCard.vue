<template>
    <div :class="'event ' + event.type"
         :id="'ev-' + event.id"
         @mouseover="isHovered = true"
         @mouseleave="isHovered = false"
         @dblclick="toggleEditor"
      >
      <div class="controls left" v-if="isHovered">
        <i v-if="editable" class="fas fa-grip-lines" ></i>
        <router-link :to="'#ev-' + event.id"><i class="fas fa-anchor"></i></router-link>
      </div>
      <div class="content">
        <div v-if="!isEditing && event.type === 'text'" v-html="markdownText"></div>
        <h1 v-if="!isEditing && event.type === 'header'" v-html="event.value"></h1>
        <EventEditor :event="event" @save="onEventSave()" v-if="editable && isEditing"></EventEditor>
      </div>
      <div class="controls right" v-if="isHovered">
        <i v-if="editable" class="fas fa-edit" @click="toggleEditor"></i>
        <i v-if="editable" class="fas fa-trash" @click="remove"></i>
        {{ event.order }}
      </div>
    </div>
</template>

<script>
  import EventEditor from './EventEditor';

  export default {
    name: "EventCard",
    components: {EventEditor},
    props: {
      event: {
        type: Object,
        default: undefined,
        required: true
      },
      editable: {
        type: Boolean,
        required: false,
        default: true
      }
    },
    data() {
      return {
        isHovered: false,
        isEditing: false
      }
    },
    mounted() {
      if (!this.$props.event.id)
        this.isEditing = true;
    },
    computed: {
      isNew: function () {
        if(!this.event)
          return true;
        return !this.event.id;
      },
      markdownText: function() {
        if (!this.isEditing && this.event.type === 'text')
          return this.$showdown.makeHtml(this.event.value);
        return this.event.value;
      }
    },
    methods: {
      onEventSave: function () {
        this.isEditing = false;
      },
      toggleEditor: function () {
        if (this.editable)
          this.isEditing = !this.isEditing;
      },
      remove: function () {
        if(this.isNew) {
          this.$emit('remove');
        }
        else {
         this.$http.delete('events/' + this.event.id + '/')
          .then(response => {
            this.$emit('remove');
          })
          .catch(error => {
            console.log(error);
          });
        }
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../main.scss";

  .event {
    /*margin-bottom: 10px;*/
    position: relative;
    display: flex;
    flex-flow: row nowrap;
    justify-content: center;
    align-items: flex-start;
    min-height: 2em;

    .content {
      width: 600px;
    }

    &:hover {
      background-color: $color2;
    }

    /* Type: text */
    &.text > .content {
      box-sizing: border-box;
    }

    /* Type: Header */
    &.header {
      margin-top: 1em;
      /*margin-bottom: 1em;*/
    }

    &.header > .content {

      /*text-align: center;*/
      /*border-radius: 10px;*/

      /*color: #2c3e50;*/
      /*background-color: white;*/
    }

    .controls {
      box-sizing: border-box;
      margin-top: 0.7em;
      width: 80px;
      display: flex;
      flex-flow: row nowrap;
      justify-content: center;

      div {
        font-size: 14px;
        font-weight: normal;
        background: $color2;
        padding: 12px;
        border-radius: 100px;
        box-shadow: 0 0px 2px rgba(0, 0, 0, 0.25);
      }

      .fas {
        cursor: pointer;
        color: $color4;
        margin: 0 5px;
      }
    }
  }
</style>
