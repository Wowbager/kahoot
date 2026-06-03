<script>
  import Router from 'svelte-spa-router';
  import Home from './pages/Home.svelte';
  import Join from './pages/Join.svelte';
  import Presenter from './pages/Presenter.svelte';
  import Display from './pages/Display.svelte';
  import Play from './pages/Play.svelte';

  const routes = {
    '/': Home,
    '/join': Join,
    '/presenter/:code': Presenter,
    '/display': Display,
    '/display/:code': Display,
    '/play/:code/:nickname': Play,
  };
</script>

<Router {routes} />
