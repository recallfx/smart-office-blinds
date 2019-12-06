<template>
  <div class="Polaris-Layout__Section">
    <div class="Polaris-Card">
      <div class="Polaris-Card__Header">
        <h2 class="Polaris-Heading">Channel list</h2>
      </div>

      <channel v-for="channel in channels"
        :key="channel.name"
        :available-actions="channel.available_actions"
        :last-action="channel.last_action"
        :label="channel.label"
        :name="channel.name"
        :status="channel.status"
        :commands="commands"
        :has-correct-domain="hasCorrectDomain"
      />
    </div>
  </div>
</template>

<script>
import Channel from "./channel.vue";

export default {
  components: {
    Channel
  },
  props: {
      channels: Array,
      commands: Array,
      hasCorrectDomain: Boolean,
  },
};
</script>