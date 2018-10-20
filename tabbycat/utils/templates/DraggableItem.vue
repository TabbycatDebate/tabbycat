<template>

  <div draggable=true class="d-flex align-items-center" style="height: 100px; width: 300px;">

    <h4 class="mb-0 pr-2 text-monospace"><slot name="number"></slot></h4>
    <div>
      <h5 class="mb-0"><slot name="title"></slot></h5>
      <small><slot name="subtitle"></slot></small>
    </div>

  </div>

</template>

<script>
export default {

}
</script>
