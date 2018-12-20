<template>
    <div class="editor">
      <textarea ref='textarea' v-model="event.value"></textarea>
      <div class="controls">
        <div class="field">
          <input type="checkbox" v-model="event.type" true-value="header" false-value="text" />
          <span>Это заголовок</span>
        </div>
        <div class="field">{{ status }}</div>
        <div v-if="!savingInProgress" class="button" @click="save"><i class="fas fa-save"></i>&nbsp; {{ buttonCaption }}</div>
        <div v-if="savingInProgress" class="button">
          <Loader />
        </div>
      </div>
    </div>
</template>

<script>
  import Loader from "./Loader";
  export default {
    name: "EventEditor",
    components: {Loader},
    props: {
      event: {
        type: Object,
        required: false,
        default: undefined
      }
    },
    data() {
      return {
        status: '',
        savingInProgress: false
      }
    },
    mounted() {
      // Focus the texarea on mount
      this.$nextTick(() => this.$refs.textarea.focus());
    },
    computed: {
      isNew: function () {
        if(!this.event)
          return true;
        return !this.event.id;
      },
      buttonCaption: function () {
        if (this.isNew)
          return 'Добавить';

        return 'Сохранить';
      }
    },
    methods: {
      save: function () {
        if(this.savingInProgress)
          return;

        this.savingInProgress = true;
        this.status = 'Сохраняем...';

        let request;
        if (this.isNew) {
          request = this.$http.post(this.event.realm + '/events/', this.$props.event);
        } else {
          request = this.$http.put('events/' + this.$props.event.id + '/', this.$props.event);
        }

        request.then(response => {
          this.status = 'Сохранено';
          this.$props.event.id = response.data.id;
          this.$props.event.order = response.data.order;
          this.$props.event.type = response.data.type;
          this.$props.event.value = response.data.value;
          this.$emit('save');
        }).catch(error => {
          this.status = 'Ошибка';
        }).finally(() => {
          this.savingInProgress = false;
        });
      }
    }
  }
</script>

<style scoped lang="scss">
    @import "../../main.scss";

  .editor {
    width: 100%;

    textarea {
      width: 100%;
      resize: vertical;
      min-height: 200px;
      max-height: 600px;
      border-radius: 5px;
      /*border: 1px solid $color4;*/
      border: 0;
      background-color: $color3;
      /*padding: 10px;*/
      box-sizing: border-box;
      font-size: 100%;
      font-family: $font-family;
      line-height: 1.5em;
    }

    .controls {
      margin-top: 5px;
      margin-bottom: 5px;
      display: flex;
      flex-flow: row nowrap;
      justify-content: space-between;
    }

    .button {
      padding: 8px 16px;
      /*width: 60px;*/
      text-align: center;
      border-radius: 5px;
      border: 1px solid $color4;
      color: $color4;
      background-color: white;
      cursor: pointer;
    }

    .field {
      color: $color4;
      padding: 8px 0px;
    }
  }
</style>
