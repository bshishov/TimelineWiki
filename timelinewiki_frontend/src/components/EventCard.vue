<template>
    <div :class="'event ' + event.type"
         :id="'ev-' + event.id"
         @mouseover="isHovered = true"
         @mouseleave="isHovered = false">
      <div>{{ event.value }}</div>
      <div class="controls" v-if="isHovered">
          <div>
            <i class="fas fa-anchor"></i>
            <i class="fas fa-grip-lines"></i>
            <i class="fas fa-edit"></i>
            <i class="fas fa-trash"></i>
          </div>
      </div>
    </div>
</template>

<script>
    export default {
      name: "EventCard",
      props: ['event'],
      data() {
        return {
          isHovered: false
        }
      },
      mounted() {
      },
    }
</script>

<style scoped lang="scss">
  @import "../../main.scss";

  .event {
    margin-bottom: 10px;
    padding: 20px;
    position: relative;
  }


  .event.text {
    border-radius: 10px;
    background-color: $color2;
  }

  .event.header {
    font-size: 32px;
    text-align: center;
    border-radius: 10px;
    font-weight: bold;
    color: #2c3e50;
    /*background-color: white;*/
  }

  .controls {
    z-index: 999;
    position: absolute;
    left: 0;
    right: 0;
    bottom: -20;

    display: flex;
    flex-flow: row nowrap;
    justify-content: center;

    /*opacity: 0;*/
    transition: opacity .5s;

    div {
      font-size: 16px;
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
</style>
