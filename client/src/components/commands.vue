<template>
    <ul v-if="commands.length > 0">
        <li v-for="command in commands" :key="timestamp(command.timestamp)">
            <div class="Polaris-Stack">
                <div class="Polaris-Stack__Item"><span class="Polaris-Badge"><span class="Polaris-Badge__Content">{{command.action}}</span></span></div>
                <div class="Polaris-Stack__Item">{{command.email}}</div>
                <div class="Polaris-Stack__Item">{{timestampToLocaleString(command.timestamp)}}</div>
            </div>
        </li>
    </ul>
</template>

<script>
import {capitalize} from '../utils';

export default {
  props: {
    commands: Array,
  },
  methods: {
      timestampToLocaleString(timestamp) {
        return timestamp.toDate().toLocaleString();
      },
      timestamp(timestamp) {
        return timestamp.toDate().getTime();
      },
  },
}
</script>