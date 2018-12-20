<template>
  <div class="outline" ref="outline">
    <a href="javascript:void(0)" class="closebtn" @click="close">&times;</a>
    <h1>Оглавление</h1>
    <div v-for="header in headers" class="item">
      <router-link :to="'#ev-' + header.id" >{{ header.value }}</router-link>
    </div>
  </div>
</template>

<script>
  export default {
    name: "Outline",
    props: {
      events: {
        type: Array,
        default: [],
        required: false
      },
      eventType: {
        type: String,
        default: 'header',
        required: false
      }
    },
    data() { return {} },
    mounted() {
      this.open();
    },
    methods: {
      open: function () {
        this.$refs.outline.style.width = '300px';
      },
      close: function (){
        this.$refs.outline.style.width = '0';
      }
    },
    computed: {
      headers: function () {
        return this.$props.events.filter(ev => ev.type === this.eventType);
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../main.scss";

  .outline {
    height: 100%;
    width: 0;
    position: fixed;
    z-index: 1;
    top: 0;
    left: 0;
    background-color: $color3;
    overflow-x: hidden;
    padding: 20px;
    box-sizing: border-box;
    transition: 0.5s;

    display: flex;
    flex-flow: column nowrap;
    justify-content: flex-start;

    .closebtn {
      position: absolute;
      top: 0;
      right: 25px;
      font-size: 36px;
      margin-left: 50px;
    }

    .item {
      font-size: 1em;
      line-height: 1.2em;
      padding: 1em 0;
      border-bottom: 1px solid $color4;

      a {
        text-decoration: none;
        color: $color5;
      }
    }
  }
</style>
