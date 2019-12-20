<template>
  <div class="Polaris-ButtonGroup__Item">
    <button
      type="button"
      :title="title"
      class="Polaris-Button"
      :class="{'Polaris-Button--disabled': disabled }"
      :disabled="disabled"
      @click="onCommandClick"
    >
      <span class="Polaris-Button__Content">
        <span class="Polaris-Button__Text">{{label}}</span>
      </span>
    </button>
  </div>
</template>

<script>
import {capitalize} from '../utils';

export default {
  props: {
    channelName: String,
    action: String,
    disabled: Boolean,
  },
  computed: {
    title() {
      return capitalize(this.action.replace(/_/g, ' '));
    },
    label() {
      switch (this.action) {
        case 'open_30_percent':
          return '30%';
        case 'open':
          return '⬆';
        case 'close':
          return '⬇';
        case 'stop':
          return '🛑';
        case 'position_toggle':
          return '🎚';
        default:
          return capitalize(this.action.replace(/_/g, ' '));
      }
    },
  },
  methods: {
    onCommandClick() {
      this.$emit('command', this.channelName, this.action);
    },
  },
}
</script>
