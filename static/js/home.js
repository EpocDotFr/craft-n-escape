var vue_delimiters = ['${', '}']; // Because Jinja2 already uses double brackets

Vue.component('recipeitem', {
    delimiters: vue_delimiters,
    template: '#recipeitem',
    props: ['items', 'recipe_item', 'escapistswikisearch']
});

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

            _.each(this.items, function(item, item_id) {
                var match = true;

                if (this.query) {
                    match = (item.name.toLowerCase().indexOf(this.query.toLowerCase()) !== -1);
                }

                if (match) {
                    filtered_items[item_id] = item;
                }
            }, this);

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
            name: '',
            is_buyable: false,
            can_heal: false,
            can_hurt: false,
            can_dig: false,
            can_chop: false,
            can_unscrew: false,
            can_cut: false,
            is_carried: false,
            is_in_desks: false,
            can_disrupt_cameras: false,
            is_outfit: false,
            is_craftable: false
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

            _.each(this.items, function(item, item_id) {
                if (('craft' in item)) {
                    _.each(item.craft.recipe_items, function(recipe_item) {
                        if (!(recipe_item.id in component_items)) {
                            component_items[recipe_item.id] = this.items[recipe_item.id];
                        }
                    }, this);
                }
            }, this);

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

            _.each(this.items, function(item, item_id) {
                var name = is_buyable = can_heal = can_hurt = can_dig = can_chop = can_unscrew = can_cut = is_carried = is_in_desks = can_disrupt_cameras = is_outfit = is_craftable = can_i_craft = true;

                if (('name' in item) && this.filters.name) {
                    name = item.name.toLowerCase().indexOf(this.filters.name.toLowerCase()) !== -1;
                }

                if (this.filters.is_buyable) {
                    is_buyable = ('buy' in item);
                }

                if (this.filters.can_heal) {
                    can_heal = ('hp' in item);
                }

                if (this.filters.can_hurt) {
                    can_hurt = ('weapon' in item);
                }

                if (this.filters.can_dig) {
                    can_dig = ('digging' in item);
                }

                if (this.filters.can_chop) {
                    can_chop = ('chipping' in item);
                }

                if (this.filters.can_unscrew) {
                    can_unscrew = ('unscrewing' in item);
                }

                if (this.filters.can_cut) {
                    can_cut = ('cutting' in item);
                }

                if (this.filters.is_carried) {
                    is_carried = ('npc_carry' in item);
                }

                if (this.filters.is_in_desks) {
                    is_in_desks = ('desk' in item);
                }

                if (this.filters.can_disrupt_cameras) {
                    can_disrupt_cameras = ('camdis' in item);
                }

                if (this.filters.is_outfit) {
                    is_outfit = ('outfit' in item);
                }

                if (this.whatCanICraft.itemsIOwn.length > 0) {
                    can_i_craft = what_can_i_craft.indexOf(item_id) !== -1;
                } else if (this.filters.is_craftable) {
                    is_craftable = ('craft' in item);
                }

                if (name && is_buyable && can_heal && can_hurt && can_dig && can_chop && can_unscrew && can_cut && is_carried && is_in_desks && can_disrupt_cameras && is_outfit && is_craftable && can_i_craft) {
                    filtered_items[item_id] = item;
                }
            }, this);

            return filtered_items;
        }
    },
    methods: {
        addItemIOwn: function() {
            // If the item to add is already present in the items I own list, just increment its amount
            var already_present = _.findIndex(this.whatCanICraft.itemsIOwn, function(itemIOwn) {
                return itemIOwn.id == this.whatCanICraft.addItem.id;
            }, this);

            if (already_present == -1) {
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
        clearAllFilters: function() {
            this.filters.name = '';
            this.filters.is_buyable = false;
            this.filters.can_heal = false;
            this.filters.can_hurt = false;
            this.filters.can_dig = false;
            this.filters.can_chop = false;
            this.filters.can_unscrew = false;
            this.filters.can_cut = false;
            this.filters.is_carried = false;
            this.filters.is_in_desks = false;
            this.filters.can_disrupt_cameras = false;
            this.filters.is_outfit = false;
            this.filters.is_craftable = false;
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
