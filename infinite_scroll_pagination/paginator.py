from django.core.paginator import EmptyPage, Page


__all__ = [
    'SeekPaginator',
    'SeekPage',
    'EmptyPage',
]


class SeekPaginator(object):

    def __init__(self, query_set, per_page, lookup_field, order='desc', use_pk=True):
        self.query_set = query_set
        self.per_page = per_page
        self.lookup_field = lookup_field
        self.order = order
        self.use_pk = use_pk

    def prepare_order(self):
        params = []

        order_prefix = '-' if self.order == 'desc' else ''
        lookup_field = '%s%s' % (order_prefix, self.lookup_field)

        params.append(lookup_field)

        if self.use_pk:
            if self.lookup_field not in ('pk', 'id'):
                params.append('%spk' % order_prefix)

        return params

    def prepare_lookup(self, value, pk=None):
        """
        Lookup:

        ...
        WHERE date <= ?
        AND NOT (date = ? AND id >= ?)
        ORDER BY date DESC, id DESC
        """
        filter_lookups = {}
        exclude_lookups = {}

        suffix = 'lt' if self.order == 'desc' else 'gt'

        if self.lookup_field not in ('pk', 'id'):
            filter_lookup = '%s__%se' % (self.lookup_field, suffix)

            exclude_lookups = {self.lookup_field: value}
            if pk is not None and self.use_pk:
                exclude_lookups['pk__gte'] = pk
        else:
            filter_lookup = '%s__%s' % (self.lookup_field, suffix)

        filter_lookups[filter_lookup] = value

        return filter_lookups, exclude_lookups

    def page(self, value=None, pk=None):
        query_set = self.query_set

        if value is not None:
            filter_lookups, exclude_lookups = self.prepare_lookup(value=value, pk=pk)

            query_set = query_set.filter(**filter_lookups)
            if exclude_lookups:
                query_set = query_set.exclude(**exclude_lookups)

        order = self.prepare_order()
        query_set = query_set.order_by(*order)[:self.per_page + 1]

        object_list = list(query_set)
        has_next = len(object_list) > self.per_page
        object_list = object_list[:self.per_page]

        if not object_list and value:
            raise EmptyPage('That page contains no results')

        return SeekPage(object_list=object_list,
                        number=value,
                        paginator=self,
                        has_next=has_next,
                        use_pk=self.use_pk)


class SeekPage(Page):

    def __init__(self, object_list, number, paginator, has_next, use_pk):
        super(SeekPage, self).__init__(object_list, number, paginator)

        self._has_next = has_next
        self._objects_left = None
        self._pages_left = None
        self._use_pk = use_pk

    def __repr__(self):
        return '<Page value %s>' % self.number or ""

    def has_next(self):
        return self._has_next

    def has_previous(self):
        raise NotImplementedError

    def has_other_pages(self):
        return self.has_next()

    def next_page_number(self):
        raise NotImplementedError

    def previous_page_number(self):
        raise NotImplementedError

    def start_index(self):
        raise NotImplementedError

    def end_index(self):
        raise NotImplementedError

    @property
    def objects_left(self):
        """
        Returns the total number of *objects* left
        """
        if not self.has_next():
            return 0

        if self._objects_left is None:
            last = self.object_list[-1]

            value = getattr(last, self.paginator.lookup_field)

            prepare_lookup_kwargs = {'value': value}
            if self._use_pk:
                prepare_lookup_kwargs['pk'] = last.pk

            filter_lookups, exclude_lookups = self.paginator.prepare_lookup(**prepare_lookup_kwargs)

            query_set = self.paginator.query_set.filter(**filter_lookups)
            if exclude_lookups:
                query_set = query_set.exclude(**exclude_lookups)

            order = self.paginator.prepare_order()

            self._objects_left = query_set.order_by(*order).count()

        return self._objects_left

    @property
    def pages_left(self):
        """
        Returns the total number of *pages* left
        """
        if not self.objects_left:
            return 0

        if self._pages_left is None:
            self._pages_left = (-self.objects_left // self.paginator.per_page) * -1  # ceil

        return self._pages_left

    def next_page_pk(self):
        return self.object_list[-1].pk
