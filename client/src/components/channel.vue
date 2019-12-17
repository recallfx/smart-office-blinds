<template>
  <div class="Polaris-Card__Section">
    <div class="Polaris-Card__SectionHeader">

      <div class="Polaris-Stack Polaris-Stack--alignmentBaseline">
        <div class="Polaris-Stack__Item Polaris-Stack__Item--fill">
          <h3 class="Polaris-Subheading">{{label}}</h3>
        </div>
        <!-- <div class="Polaris-Stack__Item" v-if="busy">
          <span class="Polaris-Badge Polaris-Badge--statusInfo"><span class="Polaris-VisuallyHidden">Info</span><span class="Polaris-Badge__Content">{{ capitalizedStatus }}</span></span>
        </div> -->
      </div>
    </div>

    <div class="Polaris-ButtonGroup">
      <action
        v-for="action in availableActions"
        :key="action"
        :channel-name="name"
        :action="action"
        :disabled="!hasCorrectDomain || busy || isCurrentActionButton(action)"
        @command="onCommand"
      />
    </div>

    <commands :commands="channelCommands" />
  </div>
</template>

<script>
import Action from "./action.vue";
import Commands from "./commands.vue";
import {capitalize} from '../utils';

const IDLE = 'idle';

export default {
  components: {
    Action,
    Commands,
  },
  props: {
    name: String,
    label: String,
    availableActions: Array,
    lastAction: String,
    status: String,
    commands: Array,
    hasCorrectDomain: Boolean,
  },
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    busy() {
      return this.loading || this.status !== IDLE;
    },
    capitalizedStatus() {
      return capitalize(this.status);
    },

    channelCommands() {
      return this.commands.filter((command) => command.channel === this.name);
    },
  },

  methods: {
    isCurrentActionButton(action) {
      return action === this.lastAction;
    },

    onCommand(channelName, action) {
      this.$set(this, 'loading', true);
      this.$root.$emit('command', channelName, action, () => {
        this.$set(this, 'loading', false);
      });
    },
  },
};
</script>
