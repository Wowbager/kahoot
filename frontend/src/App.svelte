<script>
  import Router from 'svelte-spa-router';
  import Home from './pages/Home.svelte';
  import Host from './pages/Host.svelte';
  import Presenter from './pages/Presenter.svelte';
  import Play from './pages/Play.svelte';

  const routes = {
    '/': Home,
    '/host': Host,
    '/presenter/:code': Presenter,
    '/play/:code/:nickname': Play,
  };
</script>

<Router {routes} />
