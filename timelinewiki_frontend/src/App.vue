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
    components: {Header, Footer}
  }
</script>

<style lang="scss">
  @import "../main.scss";

  body {
    color: $color5;
    background-color: $color3;
    font-family: $font-family;
  }

  a {
    color: $color1;
  }

  .container {
    padding: 10px;
    margin: 0 auto;
    width: 800px;
  }
</style>
