var vue_delimiters = ['${', '}']; // Because Jinja2 already uses double brackets

Vue.component('itemname', {
    delimiters: vue_delimiters,
    template: '#itemname',
    props: ['item', 'itemid', 'escapistswikisearch']
});

Vue.component('itemsiownfilter', {
    delimiters: vue_delimiters,
    template: '#itemsiownfilter',
    props: ['items', 'add_item'],
    data: function() {
        return {
            query: ''
        };
    },
    computed: {
        filteredItems: function() {
            var filtered_items = {};

            for (var item_id in this.items) {
                var item = this.items[item_id];
                var match = true;

                if (this.query) {
                    match = (item.name.toLowerCase().indexOf(this.query.toLowerCase()) !== -1);
                }

                if (match) {
                    filtered_items[item_id] = item;
                }
            }

            return filtered_items;
        }
    }
});

var app = new Vue({
    delimiters: vue_delimiters,
    el: '#app',
    data: {
        loading: true,
        items: items,
        recipes: recipes,
        escapistsWikiSearch: 'http://' + ESCAPISTS_WIKI_DOMAIN + '/Special:Search/',
        filters: {
            name: ''
        },
        whatCanICraft: {
            addItem: {
                id: '',
                amount: 1,
            },
            itemsIOwn: []
        }
    },
    mounted: function() {
        this.$nextTick(function () {
            this.loading = false;
        });
    },
    computed: {
        componentItems: function() {
            var component_items = {};

            for (var item_id in this.items) {
                var item = this.items[item_id];

                for (var recipe_id in this.recipes) {
                    var recipe = this.recipes[recipe_id];

                    for (var j = 0; j < recipe.items.length; j++) {
                        var recipe_item = recipe.items[j];

                        if (item_id == recipe_item.id) {
                            component_items[item_id] = item;
                        }
                    }
                }
            }

            return component_items;
        },
        filteredItems: function () {
            if (this.whatCanICraft.itemsIOwn.length > 0) {
                var what_can_i_craft = [];
                var items_i_own_ids = this.whatCanICraft.itemsIOwn.map(function(item_i_own) {
                    return item_i_own.id;
                });

                for (var recipe_id in this.recipes) {
                    var recipe = this.recipes[recipe_id];
                    var recipe_items_ids = recipe.items.map(function(recipe_item) {
                        return recipe_item.id;
                    });

                    // Items I own aren't all present in the item recipe
                    if (items_i_own_ids.sort().toString() != recipe_items_ids.sort().toString()) {
                        continue;
                    }

                    var add_to_what_can_i_craft = true;

                    for (var i = 0; i < this.whatCanICraft.itemsIOwn.length; i++) {
                        var itemIOwn = this.whatCanICraft.itemsIOwn[i];

                        for (var k = 0; k < recipe.items.length; k++) {
                            var recipe_item = recipe.items[k];

                            if (itemIOwn.id == recipe_item.id && itemIOwn.amount < recipe_item.amount) {
                                add_to_what_can_i_craft = false;
                                break;
                            }
                        }

                        if (!add_to_what_can_i_craft) {
                            break;
                        }
                    }

                    if (add_to_what_can_i_craft && !(recipe_id in what_can_i_craft)) {
                        what_can_i_craft.push(recipe_id);
                    }
                }
            }

            var filtered_items = {};

            for (var item_id in this.items) {
                var item = this.items[item_id];
                var name = can_i_craft = true;

                if (('name' in item) && this.filters.name) {
                    name = item.name.toLowerCase().indexOf(this.filters.name.toLowerCase()) !== -1;
                }

                if (this.whatCanICraft.itemsIOwn.length > 0) {
                    can_i_craft = what_can_i_craft.indexOf(item_id) !== -1;
                }

                if (name && can_i_craft) {
                    filtered_items[item_id] = item;
                }
            }

            return filtered_items;
        }
    },
    methods: {
        addItemIOwn: function() {
            // If the item to add is already present in the items I own list, just increment its amount
            var already_present = false;

            for (var i = 0; i < this.whatCanICraft.itemsIOwn.length; i++) {
                var itemIOwn = this.whatCanICraft.itemsIOwn[i];

                if (itemIOwn.id == this.whatCanICraft.addItem.id) {
                    already_present = i;
                    break;
                }
            }

            if (already_present === false) {
                this.whatCanICraft.itemsIOwn.push({
                    id: this.whatCanICraft.addItem.id,
                    amount: this.whatCanICraft.addItem.amount
                });
            } else {
                this.whatCanICraft.itemsIOwn[already_present].amount += this.whatCanICraft.addItem.amount;
            }

            this.whatCanICraft.addItem.id = '';
            this.whatCanICraft.addItem.amount = 1;
        },
        getFound: function(found) {
            switch (found) {
                case 'irongate':
                    return 'HMP-Irongate';
                break;
                case 'perks':
                    return 'Center Perks';
                break;
                case 'jungle':
                    return 'Jungle Compound';
                break;
                case 'stalagflucht':
                    return 'Stalag Flucht';
                break;
                case 'sanpancho':
                    return 'San Pancho';
                break;
                case 'escapeteam':
                    return 'Escape Team';
                break;
                case 'DTAF':
                    return 'Duct Tapes Are Forever';
                break;
                case 'SS':
                    return 'Santa\'s Sweatshop';
                break;
                default:
                    return null;
            }
        }
    }
});
