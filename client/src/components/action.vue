<template>
  <div class="Polaris-ButtonGroup__Item">
    <button
      type="button"
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
    label() {
      return capitalize(this.action.replace(/_/g, ' '))
    },
  },
  methods: {
    onCommandClick() {
      this.$emit('command', this.channelName, this.action);
    },
  },
}
</script>