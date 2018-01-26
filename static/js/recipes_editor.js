Vue.component('itemsfilter', {
    delimiters: vue_delimiters,
    template: '#itemsfilter',
    props: ['items', 'recipe_item'],
    data: function() {
        return {
            query: ''
        };
    },
    computed: {
        filteredItems: function() {
            var filtered_items = [];

            _.each(this.items, function(item, item_id) {
                var match = true;

                if (this.query) {
                    match = (item.name.toLowerCase().indexOf(this.query.toLowerCase()) !== -1) || item_id == this.query;
                }

                if (match) {
                    item.id = item_id; // The item ID is the this.items key but does not exist in the item object itself. So add it manually

                    filtered_items.push(item);
                }
            }, this);

            return filtered_items.sort(function(first_item, second_item) {
                return first_item.name.localeCompare(second_item.name);
            });
        }
    }
});

Vue.component('item', {
    delimiters: vue_delimiters,
    template: '#item',
    props: ['items', 'recipe_items', 'recipe_item']
});

var app = new Vue({
    delimiters: vue_delimiters,
    el: '#app',
    data: {
        loading: true,
        items: items,
        currentRecipe: current_recipe
    },
    mounted: function() {
        this.$nextTick(function() {
            this.loading = false;
        });
    },
    methods: {
        addItem: function(parent) {
            parent.push({
                id: '',
                amount: 1
            });
        },
        addOneOfGroup: function() {
            this.currentRecipe.items.push([]);
        }
    }
});