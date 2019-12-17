<template>
  <div class="Polaris-Card__Section">
    <div class="Polaris-Card__SectionHeader">

      <div class="Polaris-Stack Polaris-Stack--alignmentBaseline">
        <div class="Polaris-Stack__Item Polaris-Stack__Item--fill">
          <h3 class="Polaris-Subheading">{{label}}</h3>
        </div>
        <div class="Polaris-Stack__Item" v-if="busy">
          <span class="Polaris-Badge Polaris-Badge--statusInfo"><span class="Polaris-VisuallyHidden">Info</span><span class="Polaris-Badge__Content">{{ capitalizedStatus }}</span></span>
        </div>
      </div>
    </div>

    <div class="Polaris-ButtonGroup">
      <div v-if="busy"><img src="data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAgMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTcuMjI5IDEuMTczYTkuMjUgOS4yNSAwIDEwMTEuNjU1IDExLjQxMiAxLjI1IDEuMjUgMCAxMC0yLjQtLjY5OCA2Ljc1IDYuNzUgMCAxMS04LjUwNi04LjMyOSAxLjI1IDEuMjUgMCAxMC0uNzUtMi4zODV6IiBmaWxsPSIjOTE5RUFCIi8+PC9zdmc+Cg==" alt="" class="Polaris-Spinner Polaris-Spinner--colorTeal Polaris-Spinner--sizeSmall" draggable="false"><span role="status"><span class="Polaris-VisuallyHidden">Busy</span></span></div>

      <action
        v-for="action in availableActions"
        :key="action"
        :channel-name="name"
        :action="action"
        :disabled="!hasCorrectDomain || busy && isCurrentActionButton(action)"
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

    async onCommand(channelName, action) {
      this.$set(this, 'loading', true);
      await this.$root.$emit('command', channelName, action);
      this.$set(this, 'loading', false);
    },
  },

  mounted() {
    // if (this.name === 'remote_10_channel2') {
    //   this.$root.$emit('subscribe', this.name);
    // }
  },

  beforeDestroy() {
    // if (this.name === 'remote_10_channel2') {
    //   this.$root.$emit('subscribe', this.name);
    // }
  },
};
</script>
