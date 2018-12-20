<template>
  <div id="app">
    <Header></Header>
    <router-view/>
    <Footer></Footer>
  </div>
</template>

<script>
  import Footer from "./components/Footer";
  import Header from "./components/Header";

  export default {
    name: 'App',
    components: {Header, Footer},
    mounted: function() {
      // From testing, without a brief timeout, it won't work.
      setTimeout(() => this.scrollFix(this.$route.hash), 1)
    },
    methods: {
      scrollFix: function(hashbang) {
        location.href = hashbang;
      }
    }
  }
</script>

<style lang="scss">
  @import "../main.scss";

  body {
    color: $color5;
    /* background-color: $color3;*/
    background-color: white;
    font-family: $font-family;
    font-size: 100%;
  }

  a {
    color: $color1;
  }

  .container {
    margin: 0 auto;
    max-width: 900px;
  }

  p {
    line-height: 1.5em;
    margin-bottom: 1em;
  }

  h1 {
    font-size: 2em;
    line-height: 1.3em;
    margin-bottom: 0.8em;
    font-weight: bold;
  }

  em, strong {
    font-weight: bold;
  }
</style>
